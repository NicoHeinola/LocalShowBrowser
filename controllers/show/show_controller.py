import json
from controllers.base_controller import BaseController
from flask import jsonify, make_response, request
from extensions.database import db
from extensions.google_image_search import GoogleImageSearch
from extensions.jwt import JWTExtension
from helpers.show_helper import SeasonPathEncoder, ShowHelper
from models.episode import Episode
from models.season import Season
from models.show import Show
from models.show_alternate_title import ShowAlternateTitle
from models.show_cover_image import ShowCoverImage
from models.user_episode import UserEpisode


class ShowController(BaseController):
    def _register_routes(self):
        base_name = '/shows'

        @self._app.route(base_name, methods=['GET'])
        def getAllShows():
            search_term = request.args.get('searchTerm', '')

            # Query
            query = Show.query
            query = query.outerjoin(ShowAlternateTitle, Show.id == ShowAlternateTitle.show_id)
            query = query.filter(Show.title.contains(search_term) | ShowAlternateTitle.title.contains(search_term))
            shows = query.all()

            return make_response(jsonify([show.serialize for show in shows]), 200)

        @self._app.route(base_name + '/<id>', methods=['GET'])
        def getShow(id):
            search_term = request.args.get('searchTerm', '')

            # Query
            query = Show.query
            query = query.filter_by(id=id)
            query = query.outerjoin(ShowAlternateTitle, Show.id == ShowAlternateTitle.show_id)
            query = query.filter(Show.title.contains(search_term) | ShowAlternateTitle.title.contains(search_term))
            show = query.first()

            if show is None:
                return make_response(jsonify({'error': 'Show Not found!'}), 404)

            return make_response(jsonify(show.serialize), 200)

        @self._app.route(base_name + '/suggest-images', methods=['GET'])
        def auto_suggest_image_url():
            search_term = request.args.get('searchTerm', '')
            if search_term == '':
                return make_response({"error": "Missing search term!"}, 400)
            amount = int(request.args.get('amount', 10))

            fail, urls = GoogleImageSearch.fetch_image_urls(search_term, amount)

            code = 200
            if fail:
                code = 500

            return make_response(jsonify(urls), code)

        @self._app.route(base_name + '/not-added', methods=['GET'])
        @JWTExtension.admin_token_required
        def get_not_added_shows(current_user):
            shows = ShowHelper.get_all_show_paths()
            filtered_shows = []
            for show in shows:
                full_path = show.full_path
                exists = Season.query.filter_by(path=full_path).first()
                if not exists:
                    filtered_shows.append(show)

            return make_response(json.dumps(filtered_shows, cls=SeasonPathEncoder), 200)

        @self._app.route(base_name, methods=['POST'])
        @JWTExtension.admin_token_required
        def add_show(current_user):
            data = request.json
            title = data['title']
            image_url = data['image_url']

            if not title:
                return make_response({"error": "Missing show title!"}, 400)
            if not image_url:
                image_url = ""

            # Add show
            show = Show(title=title, image_url=image_url)
            db.session.add(show)
            db.session.commit()

            if image_url != "":
                image = GoogleImageSearch.download_image(image_url)
                cover_image = ShowCoverImage(cover_image=image, show_id=show.id)
                db.session.add(cover_image)
                db.session.commit()

            # Alternate titles
            if 'titles' in data:
                alternate_titles = data['titles']
                for title in alternate_titles:
                    show_alternate_title = ShowAlternateTitle(title=title['title'], show_id=show.id)
                    db.session.add(show_alternate_title)
                    db.session.commit()

            # Add seasons & episodes
            seasons = data['seasons']
            db_seasons = []  # For deletions if error
            db_episodes = []  # For deletions if error
            for season in seasons:
                # Create season
                title = season['title']  # Can be empty
                number = season['number']
                path = season['path']
                show_id = show.id
                episodes = season['episodes']

                # Revert changes
                if not number or not path or not show_id or not episodes:
                    for s in db_seasons:
                        db.session.delete(s)
                        db.session.commit()
                    db.session.delete(show)
                    db.session.commit()

                    return make_response({"error": "Missing season parameters!", "params": [title, number, path, show_id, episodes]}, 400)

                db_season = Season(title=title, number=number, show_id=show_id, path=path)
                db.session.add(db_season)
                db.session.commit()
                db_seasons.append(db_season)

                # Create episodes in season
                for episode in episodes:
                    title = episode['title']
                    number = episode['number']
                    filename = episode['filename']
                    is_special = episode['is_special']
                    season_id = db_season.id

                    # Revers changes
                    if not number or not path or not show_id or not episodes:
                        for e in db_episodes:
                            db.session.delete(e)
                            db.session.commit()
                        for s in db_seasons:
                            db.session.delete(s)
                            db.session.commit()
                        db.session.delete(show)
                        db.session.commit()
                        return make_response({"error": "Missing episode parameters!"}, 400)

                    db_episode = Episode(title=title, number=number, season_id=season_id, filename=filename, is_special=is_special)
                    db.session.add(db_episode)
                    db.session.commit()
                    db_episodes.append(episode)

            return make_response(jsonify({'status': 'ok'}), 200)

        @self._app.route(base_name + "/<show_id>", methods=['DELETE'])
        @JWTExtension.admin_token_required
        def delete_show(current_user, show_id):
            if not show_id:
                return make_response({"error": "Missing show id!"}, 400)

            # Find show
            show = Show.query.filter_by(id=show_id).first()
            if show is None:
                return make_response({"error": "Show not found!"}, 404)

            db.session.delete(show)
            db.session.commit()
            return make_response(jsonify({'status': 'ok'}), 200)

        @self._app.route(base_name + "/<show_id>/watched-episode", methods=['POST'])
        @JWTExtension.token_required
        def watched_show_episode(current_user, show_id):
            data = request.json
            season_id = data['season_id']
            episode_id = data['episode_id']
            watched = data['watched']

            if show_id is None:
                return make_response({"error": "Missing show id!"}, 400)
            if season_id is None:
                return make_response({"error": "Missing season id!"}, 400)
            if episode_id is None:
                return make_response({"error": "Missing episode id!"}, 400)
            if watched is None:
                return make_response({"error": "Missing watched id!"}, 400)

            # Find show
            episode = Episode.query.filter_by(id=episode_id, season_id=season_id).first()
            if episode is None:
                return make_response({"error": "Episode not found!"}, 404)

            user_episode = UserEpisode.query.filter_by(episode_id=episode_id, user_id=current_user.id).first()
            if not user_episode:
                user_episode = UserEpisode(episode_id=episode_id, user_id=current_user.id, watched=watched)
                db.session.add(user_episode)
            else:
                user_episode.watched = watched
            db.session.commit()
            return make_response(jsonify({'status': 'ok'}), 200)

        @self._app.route(base_name + "/<show_id>/watched-episodes", methods=['GET'])
        @JWTExtension.token_required
        def get_watched_show_episodes(current_user, show_id):
            if show_id is None:
                return make_response({"error": "Missing show id!"}, 400)

            # Query
            query = UserEpisode.query
            query = query.filter_by(user_id=current_user.id)
            query = query.filter_by(watched=True)
            query = query.outerjoin(Episode)
            query = query.outerjoin(Season, Episode.season_id == Season.id)
            query = query.filter(Season.show_id == show_id)
            user_episodes = query.all()

            return make_response(jsonify([episode.serialize for episode in user_episodes]), 200)

        @self._app.route(base_name, methods=['PUT'])
        @JWTExtension.admin_token_required
        def edit_show(current_user):
            data = request.json
            title = data['title']
            image_url = data['image_url']
            id = data['id']

            if not title:
                return make_response({"error": "Missing show title!"}, 400)
            if not image_url:
                image_url = ""
            if not id:
                return make_response({"error": "Missing show id!"}, 400)

            # Add show
            show = Show.query.filter_by(id=id).first()
            if show is None:
                return make_response({"error": "Show not found!"}, 404)

            show.title = title

            existing_show_cover_image = ShowCoverImage.query.filter_by(show_id=id).first()
            if (image_url != "" and not image_url == show.image_url) or existing_show_cover_image is None:
                image = GoogleImageSearch.download_image(image_url)
                if existing_show_cover_image is not None:
                    show_cover_image = existing_show_cover_image
                    show_cover_image.cover_image = image
                else:
                    show_cover_image = ShowCoverImage(cover_image=image, show_id=show.id)
                    db.session.add(show_cover_image)
            elif existing_show_cover_image is not None and (image_url == '' or image_url is None):
                db.session.delete(existing_show_cover_image)

            show.image_url = image_url

            # Remove old titles
            alternate_titles = data['titles']
            all_title_ids = ShowAlternateTitle.query.filter_by(show_id=id).all()
            new_title_ids = [title['id'] for title in alternate_titles if 'id' in title]
            for old_id in all_title_ids:
                if old_id.id not in new_title_ids:
                    db.session.delete(old_id)

            # Add / Edit alternate titles
            if 'titles' in data:
                for title in alternate_titles:
                    if 'id' in title:
                        show_alternate_title = ShowAlternateTitle.query.filter_by(id=title['id']).first()
                        if show_alternate_title is not None:
                            show_alternate_title.title = title['title']

                    else:
                        show_alternate_title = ShowAlternateTitle(title=title['title'], show_id=show.id)
                        db.session.add(show_alternate_title)

            # Remove old seasons and their episodes
            all_seasons = Season.query.filter_by(show_id=id).all()
            seasons = data['seasons']
            for old_season in all_seasons:

                found_season = [season for season in seasons if 'id' in season and season['id'] == old_season.id]

                if len(found_season) == 0:  # Delete all episodes and the season itself
                    for episode in old_season.episodes:
                        db.session.delete(episode)
                    db.session.delete(old_season)

                else:
                    for old_episode in old_season.episodes:  # Episode deletion checks
                        new_season_episode = [episode for episode in found_season[0]['episodes'] if 'id' in episode and episode['id'] == old_episode.id]
                        if len(new_season_episode) == 0:  # Delete the episode if not found anymore
                            db.session.delete(old_episode)

            # Add seasons & episodes
            for season in seasons:
                # Create season
                title = season['title']  # Can be empty
                number = season['number']
                path = season['path']
                episodes = season['episodes']
                show_id = show.id

                # Revert changes
                if not number or not path or not show_id or not episodes:
                    db.session.rollback()
                    return make_response({"error": "Missing season parameters!", "params": [title, number, path, show_id, episodes]}, 400)

                if 'id' in season:
                    db_season = Season.query.filter_by(id=season['id']).first()
                    if db_season is None:
                        db.session.rollback()
                        return make_response({"error": "Season not found!"}, 404)
                    db_season.title = title
                    db_season.number = number
                    db_season.path = path
                else:
                    db_season = Season(title=title, number=number, show_id=show_id, path=path)
                    db.session.add(db_season)
                    db.session.commit()

                # Create episodes in season
                for episode in episodes:
                    title = episode['title']
                    number = episode['number']
                    filename = episode['filename']
                    is_special = episode['is_special']
                    season_id = db_season.id

                    # Revers changes
                    if not number or not path or not show_id or not episodes:
                        db.session.rollback()
                        return make_response({"error": "Missing episode parameters!"}, 400)
                    if 'id' in episode:
                        db_episode = Episode.query.filter_by(id=episode['id']).first()
                        if not db_episode:
                            db.session.rollback()
                            return make_response({"error": "Episode not found!"}, 404)
                        db_episode.title = title
                        db_episode.number = number
                        db_episode.filename = filename
                        db_episode.is_special = is_special
                        db_episode.season_id = season_id
                    else:
                        db_episode = Episode(title=title, number=number, season_id=season_id, filename=filename, is_special=is_special)
                        db.session.add(db_episode)

            db.session.commit()
            return make_response(jsonify({'status': 'ok'}), 200)

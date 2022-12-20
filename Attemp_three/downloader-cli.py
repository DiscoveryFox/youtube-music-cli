import os

import click
import validators

from dotenv import load_dotenv, find_dotenv, set_key

import downloader


@click.command()
@click.option('--url', required=True, help='A url of a YouTube video or playlist')
@click.option('--output_dir', default=os.getenv('OUTPUT_DIRECTORY', None),
              help='The path to the '
                   'output directory on the '
                   'machine')
@click.option('--database_path', default=os.getenv('DATABASE_PATH', None),
              help='The path to the database')
def main(url, output_dir, database_path):
    load_dotenv()
    if not os.path.exists('.env'):
        output_dir = input('What should be your default output '
                           'directory?(Leave blank for current '
                           'directory): ')

        if output_dir == '':
            os.getcwd()

        if not os.path.isdir(output_dir):
            output_dir = os.getcwd()

        set_key('.env', 'OUTPUT_DIRECTORY',
                output_dir)

        database_path_temp = input('Path to your Database file '
                                   'with the proper'
                                   ' scheme.(If database file doesnt exist a '
                                   'new one will be created in this location.'
                                   ')')

        if not os.path.isfile(database_path_temp) and os.path.isdir(database_path_temp):
            database_path_temp = os.path.join(database_path_temp, '/songs.db')

        if database_path_temp == '':
            if '\\' in os.getcwd():
                database_path_temp = os.path.join(os.getcwd(), 'songs.db')
            else:
                database_path_temp = os.path.join(os.getcwd(), 'songs.db')

        set_key('.env', 'DATABASE_PATH',
                database_path_temp)

        load_dotenv('.env')

        output_dir = os.getenv('OUTPUT_DIRECTORY')

    if database_path is None:
        database_path = os.getenv('DATABASE_PATH')

    with downloader.YoutubeDownloader(output_dir, database_path) as youtube:
        youtube: downloader.YoutubeDownloader
        if not validators.url(url):
            print(f'Url: "{url}" is not a valid url.')
            return -1
        youtube.download(url)

if __name__ == '__main__':
    main()

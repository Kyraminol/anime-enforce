from anime_enforce import AnimeEnforce
from youtube_dl import YoutubeDL
from pathvalidate import sanitize_filename
import logging
#logging.basicConfig(
#    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
#)

logger = logging.getLogger(__name__)


def main():
    enforce = AnimeEnforce()

    text = input("Search text: ")
    results = enforce.search(text)
    print()
    for index, result in enumerate(results):
        print(f"{index + 1}) {result.name}")
    
    indexes = input("Numbers to download, comma separated (e.g.: 1, 2, 4): ")
    items = [results[int(x) - 1] for x in indexes.split(",")]
    print()

    for item in items:
        i = 1
        for section, episodes in item.episodes.items():
            indexes = input(f"Episodes: {len(episodes)}\nInput 0 for all, input -1 for last one or episodes number"
                             " to download, comma separated (e.g.: 1, 2, 4): ")
            if "0" in indexes:
                indexes = ",".join([str(x) for x in range(1, len(episodes) + 1)])
            if "-1" in indexes:
                indexes = "0"
            episodes = [episodes[int(x) - 1] for x in indexes.split(",")]
            for episode in episodes:
                outtmpl = f"downloads/{sanitize_filename(item.name)}/E{episode.number:02}.%(ext)s"
                with YoutubeDL({"hls_prefer_native": True}) as ydl:
                    ydl.params.update(outtmpl=outtmpl)
                    ydl.download([episode.download])


if __name__ == '__main__':
    main()

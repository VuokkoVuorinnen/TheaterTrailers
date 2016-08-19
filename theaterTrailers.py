#!/usr/bin/python

from __future__ import unicode_literals
import youtube_dl
import tmdbsimple as tmdb
import ConfigParser
import shutil
import re
import os
import time

# Global items
MovieDict = {}
MovieList = []
DirsDict = {}
ResultsDict = {}
search = tmdb.Search()
config = ConfigParser.ConfigParser()
config.read('theaterTrailers.cfg')

# Config Varuables
# Do not currently have the config working yet
tmdb.API_KEY = '45218221359301cd0d5bdcde79441602'
youtubePlaylist = 'https://www.youtube.com/playlist?list=PLScC8g4bqD47c-qHlsfhGH3j6Bg7jzFy-'
TheaterTrailersHome = '/opt/TheaterTrailers/' #ex '/home/<user>/TheaterTrailers/', '/User/<user>/TheaterTrailers/' or 'C:\Users\<user>\TheaterTrailers'
quietVar = False
playlistEndVar = 5
pauseRate = .25

# Sets the Current Date in ISO format
currentDate = time.strftime('%Y-%m-%d')


# Main detirmines the flow of the module
def main():
  infoDownloader(youtubePlaylist)
  
  # Querries tmdb and updates the release date in the dictionary
  for item in MovieList:
    tmdbInfo(item)
  
    for s in search.results:
      releaseDate = s['release_date']
      releaseDateList = releaseDate.split('-')
      if MovieDict[item]['Trailer Year'] == releaseDateList[0]:
        MovieDict[item]['release_date'] = releaseDate
        break
  
  # Uses info from the MovieDict to send the movie to download. Checks if its been released yet here
  for movie in MovieList:
    try:
      if currentDate < MovieDict[movie]['release_date']:
        title = movie.strip()
        trailerYear = MovieDict[movie]['Trailer Year'].strip()
        videoDownloader(MovieDict[movie]['url'], title, trailerYear)
    except KeyError as e:
      pass

  cleanup()


# Downloads the video, names it and copies the resources to the folder
def videoDownloader(string, passedTitle, yearVar):
  # Options for the video downloader
  ydl1_opts = {
    'outtmpl': TheaterTrailersHome + 'Trailers/{0} ({1})/{0}.mp4'.format(passedTitle, yearVar),
    'ignoreerrors': True,
  }
  with youtube_dl.YoutubeDL(ydl1_opts) as ydl:
    ydl.download([string])
    shutil.copy2(
      TheaterTrailersHome + 'Trailers/{0} ({1})/{0}.mp4'.format(passedTitle, yearVar),
      TheaterTrailersHome + 'Trailers/{0} ({1})/{0}-trailer.mp4'.format(passedTitle, yearVar)
      )
    shutil.copy2(
      'res/poster.jpg', 
      TheaterTrailersHome + 'Trailers/{0} ({1})/'.format(passedTitle, yearVar)
      )


# Downloads info for the videos from the playlist
def infoDownloader(playlist):
  # Options for the info downloader
  ydl_opts = {
    'skip_download': True,
    'ignoreerrors': True,
    'playliststart': 1,
    'playlistend': playlistEndVar,
    'quiet': quietVar,
    'matchtitle': '.*\\btrailer\\b.*', 
  }
  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(playlist)

  for x in info['entries']:
    MovieVar = x['title']
    MovieVar = MovieVar.replace(':', '')
    if 'Official' in MovieVar:
      regexedTitle = re.search('^.*(?=(Official))', MovieVar)
    # Throws out edge cases
    else:
      break
    trailerYear = re.search('(?<=\().*(?=\))', MovieVar)
    TempDict = { 'url' : info['entries'][info['entries'].index(x)]['webpage_url']}
    movieTitle = regexedTitle.group(0).strip()
    MovieDict[movieTitle] = TempDict
    MovieDict[movieTitle]['Trailer Year'] = trailerYear.group(0)
    MovieList.append(movieTitle)


# Returns results from tmdb
def tmdbInfo(item):
  response = search.movie(query=item)
  time.sleep(pauseRate) # Pause in seconds. TMDB has a rate limit of 40 requests per 10 seconds
  return search.results
  

# Gets a list of the movies in the directory and removes old movies
def cleanup():
  dirsList = os.listdir(TheaterTrailersHome + 'Trailers/')
  for item in dirsList:
    dirsTitle = re.search('^.*(?=(\())', item)
    dirsTitle = dirsTitle.group(0).strip()
    dirsYear = re.search('(?<=\().*(?=\))', item)
    dirsYear = dirsYear.group(0).strip()
    s = tmdbInfo(dirsTitle)
    for s in search.results:
      releaseDate = s['release_date']
      releaseDateList = releaseDate.split('-')
      if dirsYear == releaseDateList[0]:
        if releaseDate <= currentDate:
          shutil.rmtree(TheaterTrailersHome + 'Trailers/{0} ({1})'.format(dirsTitle, dirsYear))
      
      else:
        pass

      break    


if __name__ == "__main__":
  main()

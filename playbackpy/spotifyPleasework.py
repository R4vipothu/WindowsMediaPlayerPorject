#ASYNC IMPORT
import asyncio
# OTHER IMPORTS
from datetime import datetime

# WINDOWS IMPORTS
from winrt._winrt_windows_storage_streams import DataReader
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager, \
    GlobalSystemMediaTransportControlsSessionPlaybackStatus


# from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionTimelineProperties
# from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionPlaybackInfo



async def createThumbnail(thumbnail_ref): #converts reference to jpg image
    stream = await thumbnail_ref.open_read_async()  # pulling the actual stream

    reader = DataReader(stream)
    size = stream.size

    await reader.load_async(size)

    data = bytearray(size)
    reader.read_bytes(data)

    with open("albumCover.jpg", "wb") as file:  # automatically closes the file too
        file.write(data)

    reader.close()
    stream.close()

def secondsToTicks(second):
    return int(second * 1e7)

def getPositionOffset(timeLineProperties):
    lastUpdate = timeLineProperties.last_updated_time

    currentTime = datetime.now(lastUpdate.tzinfo)

    return currentTime - lastUpdate

def printPretty(currentTime, endTime):
    totalTimeSecs = endTime.total_seconds()
    currentTimeSecs = currentTime.total_seconds()

    segments = int((currentTimeSecs / totalTimeSecs) * 20)
    segDiff = 20 - segments
    print("█"*segments, end="")
    print("░"*segDiff)


# def clearTerminal():
#     os.system('cls' if os.name == 'nt' else 'clear')
#Doesn't work might fix later


async def main():

    #ask windows for the controller
    mediaController = await GlobalSystemMediaTransportControlsSessionManager.request_async()


    #ask if the media player is currently active
    session = mediaController.get_current_session()


    if session is not None:
        #initial setup
        mediaProperties = await session.try_get_media_properties_async()
        timeLineProperties =  session.get_timeline_properties()
        playbackProperties = session.get_playback_info()

        isShuffling = playbackProperties.is_shuffle_active
        STARTTIME = timeLineProperties.start_time

        currentSong = mediaProperties.title
        currentArtist = mediaProperties.artist
        currentAlbum = mediaProperties.album_title
        #reference current song



        thumbnail_ref = mediaProperties.thumbnail #pulls the reference

        if thumbnail_ref:
            await createThumbnail(thumbnail_ref)

        endTime = timeLineProperties.end_time
        while True:
            #get updated info
            mediaProperties = await session.try_get_media_properties_async()
            timeLineProperties = session.get_timeline_properties()
            playbackProperties = session.get_playback_info()
            if currentSong != mediaProperties.title: #are we on the same song
                endTime = timeLineProperties.end_time
                currentSong = mediaProperties.title
                currentAlbum = mediaProperties.album_title
                currentArtist = mediaProperties.artist
                thumbnail_ref = mediaProperties.thumbnail
                if thumbnail_ref:
                    await createThumbnail(thumbnail_ref)

            position = timeLineProperties.position #get current spot in the song
            if playbackProperties.playback_status == GlobalSystemMediaTransportControlsSessionPlaybackStatus.PLAYING:

                offset = getPositionOffset(timeLineProperties) #compensate for delayed windows update -> compare last update to current time

                position = position + offset

            print(currentSong)
            print(currentArtist)
            print(currentAlbum)
            printPretty(position, endTime)
            await asyncio.sleep(1)


        # session.try_change_playback_position_async(secondsToTicks(700)) #sets the song to x seconds
        # isShuffling = session.try_change_shuffle_active_async(not isShuffling) # turns shuffle on or off


asyncio.run(main())
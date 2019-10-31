from django.http import HttpResponse
from django.shortcuts import render, redirect
import requests
from isodate import parse_duration

# Create your views here.
from django.conf import settings


def home(request):
    videos = []
    if request.method == 'POST':
        search_text = request.POST.get('search')
        search_url = "https://www.googleapis.com/youtube/v3/search"
        search_param = {
            'part': 'snippet',
            'maxResults': 9,
            'type': 'video',
            'key': settings.YOUTUBE_DATA_API_KEY,
            'q': search_text,
        }

        video_id_list = []
        response = requests.get(search_url, params=search_param)
        if (response.json().get('items') is not None):
            for video in response.json().get('items'):
                video_id = video['id']['videoId']
                video_id_list.append(video_id)

            video_url = 'https://www.googleapis.com/youtube/v3/videos'
            find_video_param = {
                'part': 'snippet,contentDetails',
                'key': settings.YOUTUBE_DATA_API_KEY,
                'id': ','.join(video_id_list),
            }
            req = requests.get(url=video_url, params=find_video_param)

            output = req.json()['items']

            if request.POST.get('submit') == "lucky":
                return redirect('https://www.youtube.com/watch?v={}'.format(output[0]['id']))

            for op in output:
                video_info = {
                    # 'id': op['id'],
                    'url': 'https://www.youtube.com/watch?v={}'.format(op['id']),
                    'title': op['snippet']['title'],
                    'duration': parse_duration(op['contentDetails']['duration']).total_seconds() // 60,
                    'img': op['snippet']['thumbnails']['high']['url'],
                }
                videos.append(video_info)
        else:
            data = {
                'message': 'Please check API Key for YouTube '
            }
            return render(request, 'search/index.html', data)
    data = {
        'videos': videos
    }

    return render(request, 'search/index.html', data)

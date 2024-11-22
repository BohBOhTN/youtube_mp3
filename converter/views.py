import os
import subprocess
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings

def upload_file(request):
    if request.method == 'POST':
        # Get the links from the textarea input (submitted as a string)
        links_text = request.POST.get('links', '')
        links = [link.strip() for link in links_text.splitlines() if link.strip()]

        # Pass the links to the frontend
        return render(request, 'upload.html', {'links': links})

    return render(request, 'upload.html')

def process_link(request):
    """Process a single YouTube link to download as MP3."""
    link = request.GET.get('link', '').strip()
    output_dir = os.path.join(settings.MEDIA_ROOT, "downloaded_mp3s")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # Get the YouTube video title
        result = subprocess.run(
            [
                "yt-dlp",
                "--get-title",
                link,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )
        video_title = result.stdout.strip()
        
        # Sanitize the title to make it safe for filenames
        sanitized_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in video_title)

        # Set the MP3 filename using the sanitized title
        mp3_filename = f"{sanitized_title}.mp3"
        mp3_path = os.path.join(output_dir, mp3_filename)

        # Download the MP3 using yt-dlp
        subprocess.run(
            [
                "yt-dlp",
                "-x",
                "--audio-format", "mp3",
                "-o", mp3_path,
                link,
            ],
            check=True,
        )

        # Return the correct relative URL for the MP3 file
        mp3_url = f"downloaded_mp3s/{mp3_filename}"
        
        return JsonResponse({
            'status': 'success',
            'message': 'Downloaded successfully!',
            'mp3_url': mp3_url,  # URL for downloading the MP3
            'disable_button': True  # Flag to disable the button after processing
        })

    except subprocess.CalledProcessError as e:
        return JsonResponse({'status': 'error', 'message': f"Failed to process link: {e}"})

import os
import subprocess
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.conf import settings

def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        file_path = os.path.join(fs.location, filename)

        # Read and process the uploaded file
        with open(file_path, 'r') as f:
            links = [line.strip() for line in f if line.strip()]

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
        # Run yt-dlp to process the link
        mp3_filename = f"{link.split('=')[-1]}.mp3"  # Example to use video ID or something else as filename
        mp3_path = os.path.join(output_dir, mp3_filename)

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
        mp3_url = f"downloaded_mp3s/{mp3_filename}"  # Use the relative path without 'media/' twice
        
        return JsonResponse({
            'status': 'success',
            'message': 'Downloaded successfully!',
            'mp3_url': mp3_url,  # Return the correct URL for downloading
            'disable_button': True  # Send a flag to disable the button
        })

    except subprocess.CalledProcessError as e:
        return JsonResponse({'status': 'error', 'message': f"Failed to process link: {e}"})

from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from nltk.corpus import PlaintextCorpusReader
import os


app = Flask(__name__)

# Set the path to the directory containing the stopwords corpus
stopwords_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'stopwords')

# If the stopwords corpus file doesn't exist, download it from NLTK
if not os.path.exists(os.path.join(stopwords_dir, 'english')):
    from nltk.corpus import stopwords
    import shutil
    
    # Download the stopwords corpus from NLTK and copy it to the data/stopwords directory
    stopwords_corpus = stopwords.words('english')
    os.makedirs(stopwords_dir, exist_ok=True)
    stopwords_file = os.path.join(stopwords_dir, 'english')
    with open(stopwords_file, 'w') as f:
        f.write('\n'.join(stopwords_corpus))
    shutil.copy(stopwords_file, os.path.join(stopwords_dir, 'stopwords'))
    print('Stopwords downloaded and copied to data/stopwords')
else:
    print('Stopwords file already exists in data/stopwords')


# Load the stopwords corpus from the copied directory
stopwords_corpus = PlaintextCorpusReader(stopwords_dir, '.*', encoding='latin1')

# Load the stopwords from the corpus
stop_words = set(stopwords_corpus.words())


@app.route('/summary/<video_id>')
def summarize_video(video_id):
    # Download the transcript for the video ID
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        # Remove stopwords from the transcript and generate a list of filtered sentences
        filtered_transcript = []
        for entry in transcript:
            words = entry['text'].split()
            words = [word for word in words if word.lower() not in stop_words]
            if words:
                filtered_text = ' '.join(words)
                filtered_transcript.append(filtered_text)

        # Concatenate the filtered transcript into a single string
        filtered_text = ' '.join(filtered_transcript)

        # Split the filtered transcript into 4000-token chunks without splitting up words or sentences
        chunk_size = 4000
        chunks = []
        current_chunk = ''
        for word in filtered_text.split():
            if len(current_chunk) + len(word) + 1 <= chunk_size:
                current_chunk += word + ' '
            else:
                chunks.append(current_chunk.strip())
                current_chunk = word + ' '
        if current_chunk:
            chunks.append(current_chunk.strip())

        # Return the chunks as a list of strings
        return jsonify(chunks)
    except:
        return None


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))


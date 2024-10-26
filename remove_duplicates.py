from flask import Flask, request, jsonify
import os
from io import StringIO
import hashlib

app = Flask(__name__)

# Configuration
DATA_DIR = './data'
OUTPUT_DIR = os.path.join(DATA_DIR, 'removed_duplicates')
ALLOWED_EXTENSIONS = {'conll'}

# Create necessary directories
os.makedirs(OUTPUT_DIR, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_next_file_number():
    import glob
    existing_files = glob.glob(os.path.join(OUTPUT_DIR, 'cleaned_*.conll'))
    if not existing_files:
        return 1
    numbers = [int(f.split('_')[-1].split('.')[0]) for f in existing_files]
    return max(numbers) + 1

def parse_conll_content(content):
    """Parse CoNLL content into sentences"""
    sentences = []
    current_sentence = []
    
    for line in content.split('\n'):
        line = line.strip()
        
        # Skip DOCSTART
        if line.startswith('-DOCSTART-'):
            continue
            
        if line:
            current_sentence.append(line)
        elif current_sentence:  # Empty line and we have a sentence
            sentences.append('\n'.join(current_sentence))
            current_sentence = []
            
    # Add last sentence if exists
    if current_sentence:
        sentences.append('\n'.join(current_sentence))
        
    return sentences

def remove_duplicates(content):
    """Remove duplicate sentences and track removed ones"""
    # Initialize output buffers
    cleaned_output = StringIO()
    removed_output = StringIO()
    
    # Add headers
    cleaned_output.write('-DOCSTART- -X- O O\n\n')
    removed_output.write('-DOCSTART- -X- O O\n\n')
    
    # Parse into sentences
    sentences = parse_conll_content(content)
    
    # Track unique and duplicate sentences
    seen_sentences = {}  # Hash -> First occurrence index
    unique_sentences = []
    removed_sentences = []
    
    for idx, sentence in enumerate(sentences):
        # Create hash of the sentence
        sentence_hash = hashlib.md5(sentence.encode()).hexdigest()
        
        if sentence_hash not in seen_sentences:
            seen_sentences[sentence_hash] = idx
            unique_sentences.append(sentence)
        else:
            # Store duplicate with its position information
            original_pos = seen_sentences[sentence_hash] + 1  # 1-based indexing
            current_pos = idx + 1
            removed_sentences.append((sentence, original_pos, current_pos))
    
    # Write unique sentences to cleaned output
    for sentence in unique_sentences:
        cleaned_output.write(sentence + '\n\n')
    
    # Write removed sentences to removed output with position information
    for sentence, original_pos, current_pos in removed_sentences:
        removed_output.write(f"# Duplicate of sentence #{original_pos}, found at position #{current_pos}\n")
        removed_output.write(sentence + '\n\n')
    
    return (
        cleaned_output.getvalue(),
        removed_output.getvalue(),
        len(sentences),
        len(unique_sentences),
        len(removed_sentences)
    )

@app.route('/deduplicate', methods=['POST'])
def deduplicate_file():
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file provided'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'No selected file'
        }), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': 'Invalid file type. Only .conll files are allowed'
        }), 400
    
    try:
        # Read the content
        content = file.read().decode('utf-8')
        
        # Process the content
        cleaned_content, removed_content, original_count, unique_count, removed_count = remove_duplicates(content)
        
        # Get next file number and create formatted number string
        file_number = get_next_file_number()
        formatted_number = f"{file_number:04d}"
        
        # Create output filenames
        cleaned_filename = f"cleaned_{formatted_number}.conll"
        removed_filename = f"removed_sentences_{formatted_number}.conll"
        
        # Create full paths
        cleaned_path = os.path.join(OUTPUT_DIR, cleaned_filename)
        removed_path = os.path.join(OUTPUT_DIR, removed_filename)
        
        # Save the files
        with open(cleaned_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
            
        with open(removed_path, 'w', encoding='utf-8') as f:
            f.write(removed_content)
        
        # Return success response with file information
        return jsonify({
            'success': True,
            'message': 'File deduplicated successfully',
            'cleaned_file': {
                'path': cleaned_path,
                'filename': cleaned_filename
            },
            'removed_sentences_file': {
                'path': removed_path,
                'filename': removed_filename
            },
            'statistics': {
                'original_sentences': original_count,
                'unique_sentences': unique_count,
                'duplicates_removed': removed_count
            },
            'status': 'Deduplicated successfully'
        })
    
    except UnicodeDecodeError:
        return jsonify({
            'success': False,
            'error': 'Invalid file encoding. File must be UTF-8 encoded'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5005)
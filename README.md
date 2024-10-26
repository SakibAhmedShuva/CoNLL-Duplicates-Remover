# CoNLL-Duplicates-Remover

A Flask-based web service that efficiently removes duplicate sentences from CoNLL format files while preserving the original structure and maintaining detailed tracking of removed duplicates.

## Features

- **Duplicate Detection**: Efficiently identifies and removes duplicate sentences while preserving CoNLL formatting
- **Detailed Tracking**: Maintains records of removed duplicates with their original positions
- **File Management**: Automatically handles file numbering and organization
- **API Support**: Simple REST API for easy integration
- **UTF-8 Support**: Full support for UTF-8 encoded files
- **Statistics**: Provides detailed statistics about the deduplication process

## Installation

1. Clone the repository:
```bash
git clone https://github.com/SakibAhmedShuva/CoNLL-Duplicates-Remover.git
cd CoNLL-Duplicates-Remover
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install flask
```

## Usage

### Starting the Server

Run the Flask application:
```bash
python remove_duplicates.py
```

The server will start on `http://localhost:5005` by default.

### API Endpoints

#### POST /deduplicate
Removes duplicates from a CoNLL file.

**Request**:
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: 
  - `file`: CoNLL format file (`.conll` extension)

**Response**:
```json
{
    "success": true,
    "message": "File deduplicated successfully",
    "cleaned_file": {
        "path": "./data/removed_duplicates/cleaned_0001.conll",
        "filename": "cleaned_0001.conll"
    },
    "removed_sentences_file": {
        "path": "./data/removed_duplicates/removed_sentences_0001.conll",
        "filename": "removed_sentences_0001.conll"
    },
    "statistics": {
        "original_sentences": 100,
        "unique_sentences": 90,
        "duplicates_removed": 10
    },
    "status": "Deduplicated successfully"
}
```

#### GET /health
Health check endpoint.

**Response**:
```json
{
    "status": "healthy"
}
```

## Output Files

The service generates two files for each processed document:

1. **Cleaned File** (`cleaned_XXXX.conll`):
   - Contains all unique sentences
   - Maintains original CoNLL format
   - Includes DOCSTART header

2. **Removed Sentences File** (`removed_sentences_XXXX.conll`):
   - Lists all removed duplicate sentences
   - Includes position information for each duplicate
   - Maintains original formatting
   - Contains comments indicating original positions

## File Structure

```
CoNLL-Duplicates-Remover/
├── data/
│   └── removed_duplicates/
├── remove_duplicates.py
└── README.md
```

## Error Handling

The service handles various error cases:
- Invalid file types (non-CoNLL files)
- Incorrect file encoding (non-UTF-8)
- Missing files
- Server errors

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Flask
- Inspired by the need for clean NLP datasets
- Designed for CoNLL format compatibility

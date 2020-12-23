# Paperless

This is an OCR service that reads images and ocr's them and creates a PDF.

## Testing

```
curl -F 'scans[]=@images/test1.jpg' -F 'scans[]=@images/test2.jpg' http://127.0.0.1:8080/pdf
```


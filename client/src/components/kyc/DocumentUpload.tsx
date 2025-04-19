
import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Upload, X, Check, File } from "lucide-react";

type DocumentType = "id_front" | "id_back" | "selfie";

interface DocumentUploadProps {
  documentType: DocumentType;
  onUpload: (type: DocumentType, file: File) => void;
  isUploaded?: boolean;
  isLoading?: boolean;
}

export function DocumentUpload({
  documentType,
  onUpload,
  isUploaded = false,
  isLoading = false,
}: DocumentUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const documentLabels = {
    id_front: "ID Card (Front)",
    id_back: "ID Card (Back)",
    selfie: "Selfie with ID",
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      handleFile(droppedFile);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (selectedFile: File) => {
    setFile(selectedFile);
    onUpload(documentType, selectedFile);
  };

  return (
    <Card className={`${dragActive ? 'border-wallet-primary' : ''}`}>
      <CardContent className="p-6">
        <div
          className="flex flex-col items-center justify-center p-6 border-2 border-dashed rounded-md"
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
        >
          {isUploaded ? (
            <div className="flex flex-col items-center space-y-2 text-wallet-success">
              <Check className="h-10 w-10" />
              <p className="font-medium">Document Uploaded</p>
              {file && <p className="text-sm text-muted-foreground">{file.name}</p>}
            </div>
          ) : file ? (
            <div className="flex flex-col items-center space-y-2">
              <File className="h-10 w-10 text-wallet-primary" />
              <p className="font-medium">{file.name}</p>
              <p className="text-sm text-muted-foreground">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          ) : (
            <div className="flex flex-col items-center space-y-2">
              <Upload className="h-10 w-10 text-muted-foreground" />
              <p className="font-medium">Upload {documentLabels[documentType]}</p>
              <p className="text-sm text-center text-muted-foreground">
                Drag & drop or click to select a file
              </p>
            </div>
          )}
          
          <input
            id={`file-upload-${documentType}`}
            type="file"
            className="hidden"
            accept="image/*"
            onChange={handleChange}
          />
        </div>
      </CardContent>
      <CardFooter className="flex justify-between">
        <Label
          htmlFor={`file-upload-${documentType}`}
          className="cursor-pointer text-wallet-primary hover:text-wallet-accent"
        >
          {file ? "Replace file" : "Select file"}
        </Label>
        
        {file && !isUploaded && (
          <Button
            variant="ghost"
            size="sm"
            className="text-destructive"
            onClick={() => setFile(null)}
          >
            <X className="h-4 w-4 mr-1" /> Remove
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}

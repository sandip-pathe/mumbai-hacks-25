"use client";

import { useCallback } from "react";
import { Card } from "@/components/ui/card";
import { Upload, FileText, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface Props {
  onFileSelect: (file: File) => void;
  isLoading: boolean;
}

export function UploadZone({ onFileSelect, isLoading }: Props) {
  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      const file = e.dataTransfer.files[0];
      if (file?.type === "application/pdf") {
        onFileSelect(file);
      }
    },
    [onFileSelect]
  );

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileSelect(file);
    }
  };

  return (
    <Card
      className={cn(
        "border-2 border-dashed p-12 text-center cursor-pointer transition-all",
        "hover:border-accent hover:bg-blue-50",
        isLoading && "opacity-50 cursor-not-allowed"
      )}
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
    >
      {isLoading ? (
        <div className="space-y-4">
          <Loader2 className="mx-auto animate-spin text-accent" size={48} />
          <div>
            <p className="text-lg font-semibold text-text-dark">
              Processing document...
            </p>
            <p className="text-sm text-gray-500 mt-1">
              AI agents are analyzing your file
            </p>
          </div>
        </div>
      ) : (
        <>
          <Upload className="mx-auto mb-4 text-gray-400" size={48} />
          <h3 className="text-xl font-heading font-bold text-text-dark mb-2">
            Upload Document for Review
          </h3>
          <p className="text-gray-600 mb-6">
            Drag and drop a PDF, or click to browse
          </p>

          <label className="inline-block">
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileInput}
              className="hidden"
              disabled={isLoading}
            />
            <span className="px-6 py-3 bg-gradient-accent text-white rounded-lg font-medium cursor-pointer hover:opacity-90 transition-opacity inline-flex items-center gap-2">
              <FileText size={18} />
              Select PDF File
            </span>
          </label>

          <p className="text-xs text-gray-500 mt-4">
            Supported: PDF files only • Max size: 10MB
          </p>
        </>
      )}
    </Card>
  );
}

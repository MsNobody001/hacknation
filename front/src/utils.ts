import { UploadFile } from "./types";

export const isValidEmail = (email: string) => {
  return /\S+@\S+\.\S+/.test(email);
};

export const formatTime = (date: Date) => {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

export const convertDate = (dateStr: string) => {
  const [day, month, year] = dateStr.split('.');
  return `${year}-${month}-${day}`;
}

export const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const simulateUpload = (file: UploadFile, onUpdate: (id: string, update: Partial<UploadFile>) => void) => {
  return new Promise((resolve, reject) => {
    const shouldFail = Math.random() < 0.05;
    let currentProgress = 0;

    onUpdate(file.id, { status: 'uploading' });

    const interval = setInterval(() => {
      currentProgress += Math.floor(Math.random() * 10) + 1; // Increment progress
      const newProgress = Math.min(currentProgress, 100);

      onUpdate(file.id, { progress: newProgress });

      if (newProgress === 100) {
        clearInterval(interval);

        if (shouldFail) {
          setTimeout(() => {
            onUpdate(file.id, { status: 'error' });
            reject(new Error(`Upload failed for ${file.name}`));
          }, 500);
        } else {
          setTimeout(() => {
            onUpdate(file.id, { status: 'complete' });
            resolve(file.id);
          }, 300);
        }
      }
    }, 150);
  });
};
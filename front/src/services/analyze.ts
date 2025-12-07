import axios from "axios";

const ANALYZE_API_URL = 'https://webapp-clerk-assistant-hhezgzg9gzcrckfs.swedencentral-01.azurewebsites.net/api/analyses/';

export interface CreateAnalyzeResponse {
  id: string,
}

export const analyzeService = {
  uploadFiles: async (id: string, files: File[], options?: {
    onProgress: (progress: number) => void;
  }) => {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable && options?.onProgress) {
          const percentComplete = (e.loaded / e.total) * 100;
          options?.onProgress(percentComplete);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          resolve(JSON.parse(xhr.responseText));
        } else {
          reject(new Error(`Upload failed: ${xhr.status}`));
        }
      });

      xhr.addEventListener('error', () => reject(new Error('Upload failed')));

      xhr.open('POST', `${ANALYZE_API_URL}${id}/documents/`);
      xhr.send(formData);
    });
  },
  create: async () => {
    const response = await axios.post<CreateAnalyzeResponse>(ANALYZE_API_URL)
    return response.data;
  },
  processing: async (id: string) => {
    const response = await axios.post<{ date: unknown }>(`${ANALYZE_API_URL}${id}/processing/`)
    return response.data;
  },
  getFormalAnalysis: async (id: string) => {
    const response = await axios.post<{ date: unknown }>(`${ANALYZE_API_URL}${id}/formal-analysis/`)
    return response.data;
  }
};

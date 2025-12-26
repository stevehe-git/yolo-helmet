import api from './index'

export interface Dataset {
  id: number
  name: string
  description?: string
  image_count: number
  file_size?: number
  status?: string
  train_count?: number
  val_count?: number
  test_count?: number
  error_reason?: string  // 验证失败原因
  created_at: string
}

export interface DatasetImage {
  filename: string
  size: number
  created_at: string
}

export interface DatasetImagesResponse {
  images: DatasetImage[]
  total: number
}

export const datasetApi = {
  getDatasets: () => api.get<Dataset[]>('/datasets'),
  getDataset: (id: number) => api.get<Dataset>(`/datasets/${id}`),
  createDataset: (data: { name: string; description?: string }) => api.post<Dataset>('/datasets', data),
  updateDataset: (id: number, data: { name?: string; description?: string }) => api.put<Dataset>(`/datasets/${id}`, data),
  deleteDataset: (id: number) => api.delete(`/datasets/${id}`),
  uploadDataset: (id: number, formData: FormData) => api.post(`/datasets/${id}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000
  }),
  getDatasetImages: (id: number) => api.get<DatasetImagesResponse>(`/datasets/${id}/images`),
  getDatasetImageUrl: (id: number, filename: string) => `/api/datasets/${id}/images/${filename}`,
  deleteDatasetImage: (id: number, filename: string) => api.delete(`/datasets/${id}/images/${filename}`)
}


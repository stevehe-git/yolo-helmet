import api from './index'

export interface Dataset {
  id: number
  name: string
  description?: string
  image_count: number
  created_at: string
}

export const datasetApi = {
  getDatasets: () => api.get<Dataset[]>('/datasets'),
  getDataset: (id: number) => api.get<Dataset>(`/datasets/${id}`),
  createDataset: (data: { name: string; description?: string }) => api.post<Dataset>('/datasets', data),
  deleteDataset: (id: number) => api.delete(`/datasets/${id}`),
  uploadDataset: (id: number, formData: FormData) => api.post(`/datasets/${id}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000
  })
}


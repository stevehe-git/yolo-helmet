import api from './index'

export interface Model {
  id: number
  name: string
  type: 'general' | 'custom'
  path: string
  description?: string
  created_at: string
  status?: 'pending' | 'training' | 'completed' | 'published' | 'failed'
  dataset_name?: string
  metrics?: {
    map?: number
    precision?: number
    recall?: number
    f1?: number
    error?: string
  }
  training_params?: {
    dataset_id?: number
    base_model?: string
    epochs?: number
    batch?: number
    imgsz?: number
  }
}

export interface ModelTrainingData {
  epochs: number[]
  train_loss: number[]
  val_loss: number[]
  map: number[]
  precision: number[]
  recall: number[]
}

export const modelApi = {
  getModels: (search?: string, status?: string) => {
    const params: any = {}
    if (search) params.search = search
    if (status) params.status = status
    return api.get<Model[]>('/models', { params })
  },
  getModel: (id: number) => api.get<Model>(`/models/${id}`),
  createModel: (data: { name: string; type?: string; description?: string; dataset_id?: number; base_model?: string; epochs?: number; batch?: number; imgsz?: number }) => api.post<Model>('/models', data),
  importModel: (formData: FormData) => api.post('/models/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000
  }),
  updateModel: (id: number, data: { name?: string; type?: string; description?: string; training_params?: any }) => api.put<Model>(`/models/${id}`, data),
  deleteModel: (id: number) => api.delete(`/models/${id}`),
  trainModel: (data: { model_id: number; dataset_id?: number; epochs?: number; batch?: number; imgsz?: number; base_model?: string }) => 
    api.post('/models/train', data),
  publishModel: (id: number) => api.post(`/models/${id}/publish`),
  unpublishModel: (id: number) => api.post(`/models/${id}/unpublish`),
  getModelTrainingData: (id: number) => api.get<ModelTrainingData>(`/models/${id}/training`),
  getModelMetrics: (id: number) => api.get(`/models/${id}/metrics`)
}


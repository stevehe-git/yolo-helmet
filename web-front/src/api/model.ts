import api from './index'

export interface Model {
  id: number
  name: string
  type: 'general' | 'custom'
  path: string
  created_at: string
  metrics?: {
    map: number
    precision: number
    recall: number
    f1: number
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
  getModels: () => api.get<Model[]>('/models'),
  getModel: (id: number) => api.get<Model>(`/models/${id}`),
  createModel: (data: { name: string; type: string }) => api.post<Model>('/models', data),
  deleteModel: (id: number) => api.delete(`/models/${id}`),
  trainModel: (data: { model_id: number; dataset_id: number; epochs: number }) => 
    api.post('/models/train', data),
  getModelTrainingData: (id: number) => api.get<ModelTrainingData>(`/models/${id}/training`),
  getModelMetrics: (id: number) => api.get(`/models/${id}/metrics`)
}


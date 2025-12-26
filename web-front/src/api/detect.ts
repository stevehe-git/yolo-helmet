import api from './index'

export interface DetectRequest {
  model_id?: number
  image?: File
  video?: File
}

export interface DetectResult {
  image: string // base64 encoded image
  detections: Detection[]
  stats: {
    total: number
    with_helmet: number
    without_helmet: number
  }
}

export interface Detection {
  class: string
  confidence: number
  bbox: [number, number, number, number] // x1, y1, x2, y2
}

export interface VideoDetectResult {
  video_url: string
  frame_results: DetectResult[]
  summary: {
    total_frames: number
    total_detections: number
    with_helmet: number
    without_helmet: number
  }
}

export const detectApi = {
  detectImage: (formData: FormData) => api.post<DetectResult>('/detect/image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  detectVideo: (formData: FormData) => api.post<VideoDetectResult>('/detect/video', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000 // 5 minutes for video processing
  }),
  startRealtime: (modelId?: number, confidence?: number, fps?: number) => api.post('/detect/realtime/start', { 
    model_id: modelId,
    confidence: confidence,
    fps: fps
  }),
  stopRealtime: () => api.post('/detect/realtime/stop'),
  getRealtimeFrame: (confidence?: number, fps?: number) => api.get<{ image: string; detections: Detection[] }>('/detect/realtime/frame', {
    params: { confidence: confidence, fps: fps }
  })
}


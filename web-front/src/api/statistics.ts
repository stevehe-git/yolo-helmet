import api from './index'

export interface Statistics {
  total_detections: number
  with_helmet: number
  without_helmet: number
  detection_rate: number
  daily_stats: {
    date: string
    count: number
  }[]
}

export const statisticsApi = {
  getStatistics: () => api.get<Statistics>('/statistics'),
  getDetectionHistory: (days?: number) => api.get('/statistics/history', { params: { days } })
}


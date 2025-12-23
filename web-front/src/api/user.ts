import api from './index'

export interface UserInfo {
  id: number
  username: string
  email?: string
  role: 'admin' | 'user'
  created_at: string
}

export const userApi = {
  getUsers: () => api.get<UserInfo[]>('/users'),
  getUser: (id: number) => api.get<UserInfo>(`/users/${id}`),
  createUser: (data: { username: string; password: string; email?: string; role?: string }) => 
    api.post<UserInfo>('/users', data),
  updateUser: (id: number, data: Partial<UserInfo>) => api.put<UserInfo>(`/users/${id}`, data),
  deleteUser: (id: number) => api.delete(`/users/${id}`)
}


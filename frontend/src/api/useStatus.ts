import { useQuery } from '@tanstack/react-query';
import apiClient from './client';
import type { SystemStatus } from '../types';

export default function useStatus() {
  return useQuery({
    queryKey: ['status'],
    queryFn: async () => {
      const response = await apiClient.get<SystemStatus>('/status');
      return response.data;
    },
    refetchInterval: 2000, // Poll every 2 seconds for real-time status updates
  });
}

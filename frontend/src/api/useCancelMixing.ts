import { useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from './client';

export default function useCancelMixing() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      await apiClient.post('/status/cancel');
    },
    onSuccess: () => {
      // Invalidate status to refresh the mixing state
      queryClient.invalidateQueries({ queryKey: ['status'] });
    },
  });
}

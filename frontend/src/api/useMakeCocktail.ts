import { useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from './client';
import type { MakeCocktailRequest } from '../types';

export default function useMakeCocktail() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ name, sizeMl }: { name: string; sizeMl: number }) => {
      const request: MakeCocktailRequest = { size_ml: sizeMl };
      await apiClient.post(
        `/cocktails/${encodeURIComponent(name)}/make`,
        request
      );
    },
    onSuccess: () => {
      // Invalidate status to refresh the mixing state
      queryClient.invalidateQueries({ queryKey: ['status'] });
    },
  });
}

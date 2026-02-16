import { useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from './client';
import type { MakeCocktailRequest } from '../types';

type Options = { name: string; size_multiplier: number };

export default function useMakeCocktail() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ name, size_multiplier }: Options) => {
      const request: MakeCocktailRequest = { size_multiplier };

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

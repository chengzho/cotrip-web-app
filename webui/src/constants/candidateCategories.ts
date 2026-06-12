export const CANDIDATE_CATEGORIES = [
  'attraction',
  'restaurant',
  'accommodation',
  'transport',
  'other',
] as const;

export type CandidateCategory = typeof CANDIDATE_CATEGORIES[number];

export const CATEGORY_LABEL: Record<CandidateCategory, string> = {
  attraction: '景點',
  restaurant: '餐廳',
  accommodation: '住宿',
  transport: '交通',
  other: '其他',
};

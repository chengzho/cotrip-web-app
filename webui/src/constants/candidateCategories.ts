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

export const RESTAURANT_MEAL_TIMES = [
  'breakfast',
  'lunch',
  'dinner',
  'snack',
  'late_night',
  'any',
] as const;

export type RestaurantMealTime = typeof RESTAURANT_MEAL_TIMES[number];

export const MEAL_TIME_LABEL: Record<RestaurantMealTime, string> = {
  breakfast: '早餐',
  lunch: '午餐',
  dinner: '晚餐',
  snack: '下午茶／點心',
  late_night: '宵夜',
  any: '不限',
};

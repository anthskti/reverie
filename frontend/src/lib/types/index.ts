export interface GlobalStats {
  total_water_saved_l: number;
  total_co2_offset_kg: number;
  total_landfill_diverted_kg: number;
}

export interface UserStats {
  user_id: string;
  water_saved_l: number;
  co2_offset_kg: number;
  landfill_diverted_kg: number;
  updated_at: string;
}

export interface Item {
  id: string;
  user_id: string;
  original_image_url: string | null;
  style: string | null;
  difficulty: string | null;
  fabric_type: string | null;
  weight_kg: number | null;
  item_type: string;
  is_market_eligible: boolean;
  created_at: string;
}

export interface UpcycleOption {
  title: string;
  description: string;
  techniques: string[];
  difficulty: string;
  mockup_url: string | null;
}

export interface IdeationResponse {
  item_id: string;
  options: UpcycleOption[];
  mockup_urls: (string | null)[];
  original_image_url: string | null;
}

export interface ExecutionRequest {
  item_id: string;
  selected_concept: UpcycleOption;
  fabric_type: string;
  weight_kg: number;
}

export interface EnvironmentalData {
  water_saved_liters?: number;
  co2_offset_kg?: number;
  landfill_diverted_kg?: number;
}

export interface ExecutionResponse {
  project_id: string | null;
  sewing_guide: string;
  environmental_impact: string;
  environmental_data: EnvironmentalData | null;
  mockup_url: string | null;
}

export interface VerificationResponse {
  score: number;
  is_eligible: boolean;
  feedback: string;
}

export interface Project {
  id: string;
  item_id: string | null;
  selected_concept: UpcycleOption;
  sewing_guide: string | null;
  environmental_impact: string | null;
  environmental_data: EnvironmentalData | null;
  created_at: string | null;
}

export interface ProjectsResponse {
  projects: Project[];
}

export type ListingCategory = "upcycled_clothing" | "material" | "tool";

export interface Listing {
  listing_id: string;
  item_id: string | null;
  seller_id: string;
  buyer_id: string | null;
  title: string;
  description: string | null;
  category: ListingCategory;
  price_usdc: number;
  status: string;
  transaction_id: string | null;
  item_style: string | null;
  item_type: string | null;
  item_image_url: string | null;
  created_at: string | null;
}

export interface ListItemRequest {
  title: string;
  description?: string;
  price_usdc: number;
  category: ListingCategory;
  item_id?: string;
}

export interface DepositSession {
  mode: string;
  session_id: string;
  external_user_id: string;
  recipient_address: string;
  destination_chain_type: string;
  destination_chain_id: string;
  destination_token_address: string;
  destination_token_symbol: string;
  amount_usdc: number;
  listing_id: string;
  seller_id: string;
}

export interface CheckoutResponse {
  listing_id: string;
  status: string;
  mode: string;
  deposit: DepositSession;
}

export interface ConfirmPaymentResponse {
  listing_id: string;
  status: string;
  transaction_id: string;
  message: string;
}

export interface ApiError {
  message: string;
  status: number;
}

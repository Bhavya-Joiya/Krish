export type StatusType = 'connected' | 'offline' | 'pending';

export interface StatCardData {
  label: string;
  value: string;
  icon: string;
  trend?: string;
  badge?: string;
}

export interface FeatureCardData {
  id: string;
  icon: string;
  title: string;
  description: string;
  tag: 'Live' | 'Roadmap';
}

export interface ChannelData {
  id: string;
  name: string;
  icon: string;
  status: StatusType;
  meta1: string;
  meta2: string;
  /** Deep link or path — Telegram t.me / Web Chat /chat */
  href?: string | null;
  actionLabel?: string;
  disabled?: boolean;
  /** Optional setup / coming-soon note */
  note?: string | null;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  message: string;
  type: 'diagnosis' | 'connection' | 'alert' | 'voice';
}

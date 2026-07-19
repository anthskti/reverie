export function TreeLine({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 1440 120"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      preserveAspectRatio="none"
      aria-hidden
    >
      <path
        d="M0 120V80C120 60 180 90 280 70C380 50 420 85 520 65C620 45 680 75 780 55C880 35 940 70 1040 50C1140 30 1200 65 1320 45L1440 35V120H0Z"
        fill="currentColor"
        opacity="0.15"
      />
      <path
        d="M0 120V95C100 80 200 105 320 88C440 71 500 98 620 82C740 66 820 95 940 78C1060 61 1140 92 1280 76L1440 68V120H0Z"
        fill="currentColor"
        opacity="0.25"
      />
    </svg>
  );
}

export function TreeSilhouette({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 64 96"
      fill="currentColor"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden
    >
      <path d="M32 8C28 8 24 12 22 18C18 16 14 18 12 22C8 24 6 28 8 32C4 34 2 38 4 42C2 46 4 50 8 52C6 58 10 64 16 66C14 72 18 78 24 80V96H40V80C46 78 50 72 48 66C54 64 58 58 56 52C60 50 62 46 60 42C62 38 60 34 56 32C58 28 56 24 52 22C50 18 46 16 42 18C40 12 36 8 32 8Z" />
    </svg>
  );
}

export function FloatingLeaf({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="currentColor"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden
    >
      <path d="M17 2C13 2 9 4 6 8C3 12 2 17 3 22C8 21 13 18 17 14C21 10 22 5 17 2ZM8 16C10 13 13 10 16 8C14 11 12 14 8 16Z" />
    </svg>
  );
}

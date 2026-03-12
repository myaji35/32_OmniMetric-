interface BadgeProps {
  label: string;
  color: string;
}

export default function Badge({ label, color }: BadgeProps) {
  return (
    <span
      className="px-2 py-0.5 rounded text-xs font-medium text-white"
      style={{ background: color }}
    >
      {label}
    </span>
  );
}

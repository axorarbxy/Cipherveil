function StatusCard({
  title,
  value,
  icon,
  type = "normal",
  subtitle,
}) {
  return (
    <div className={`status-card ${type}`}>
      
      <div className="status-card-header">
        <div className="status-icon">
          {icon}
        </div>

        <span className="status-title">
          {title}
        </span>
      </div>

      <div className="status-value">
        {value}
      </div>

      <div className="status-subtitle">
        {subtitle}
      </div>

    </div>
  );
}

export default StatusCard;
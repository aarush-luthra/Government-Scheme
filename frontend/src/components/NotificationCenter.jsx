export function NotificationCenter({ notifications }) {
  return (
    <section className="card">
      <h2>Notification Center</h2>
      <ul data-testid="notification-list">
        {notifications.length === 0 ? <li>No notifications</li> : notifications.map((n) => <li key={n.id}>{n.text}</li>)}
      </ul>
    </section>
  );
}

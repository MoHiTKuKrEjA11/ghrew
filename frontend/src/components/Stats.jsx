export default function Stats({ items }) {
  return (
    <dl className="stats">
      {items.map((s) => (
        <div key={s.label} className="stat">
          <dt>{s.label}</dt>
          <dd>{s.value}</dd>
          {s.note && <p>{s.note}</p>}
        </div>
      ))}
    </dl>
  );
}

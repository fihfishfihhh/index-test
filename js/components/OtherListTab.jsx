// OtherListTab component
function OtherListTab() {
  return (
    <div className="space-y-6">
      <div className="border-b pb-4">
        <h2 className="text-xl font-bold uppercase">OTHER LIST (CHALLENGES & PLATFORMERS)</h2>
        <p className="text-xs text-gray-500">Community challenge levels and platformer rankings.</p>
      </div>
      <div className="space-y-3">
        {[
          { rank: 1, name: "3-Frame Challenge", creator: "GD_Pro", type: "Challenge" },
          { rank: 2, name: "Tower of Trial", creator: "PlatformKing", type: "Platformer" }
        ].map(item => (
          <div key={item.rank} className="border p-4 flex justify-between items-center">
            <div>
              <div className="font-bold">{item.name} ({item.type})</div>
              <div className="text-xs text-gray-500">Creator: {item.creator}</div>
            </div>
            <span className="bg-gray-100 border text-xs font-mono px-3 py-1">RANK #{item.rank}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

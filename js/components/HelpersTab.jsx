// HelpersTab component
function HelpersTab({ helpers }) {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold uppercase border-b pb-4">FIND COMMUNITY HELPERS</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {helpers.map(h => (
          <div key={h.id} className="border-2 border-black p-4 flex justify-between items-center">
            <div>
              <div className="font-bold">{h.name}</div>
              <div className="text-xs text-gray-600">{h.role}</div>
              <div className="text-xs font-mono text-gray-500 mt-1">Discord: {h.contact}</div>
            </div>
            <span className="bg-black text-white text-xs px-3 py-1 font-bold">{h.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

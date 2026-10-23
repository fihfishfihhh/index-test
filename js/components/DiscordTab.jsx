// DiscordTab component
function DiscordTab() {
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="border-2 border-black p-6 text-center space-y-4">
        <h2 className="text-2xl font-black uppercase">JOIN FIH DISCORD SERVER</h2>
        <p className="text-sm text-gray-600">Connect with GD creators, submit your levels, find collaboration partners, and climb the Demon List rankings.</p>
        <div className="bg-gray-100 border p-4 text-left font-mono text-xs space-y-2">
          <div className="font-bold">SERVER RULES:</div>
          <div>1. Respect all players and creators.</div>
          <div>2. Submit valid video proof for list verifications.</div>
          <div>3. No stolen layouts or unauthorized re-uploads.</div>
        </div>
        <button className="bg-black text-white font-bold px-6 py-3 text-sm uppercase hover:bg-gray-800 transition">
          ACCEPT DISCORD INVITE
        </button>
      </div>
    </div>
  );
}

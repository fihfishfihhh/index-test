// SubmitTab component
function SubmitTab({ submissions, showSubmitModal, setShowSubmitModal, newSubmission, setNewSubmission, handleCreateSubmission }) {
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex justify-between items-center border-b pb-4">
        <h2 className="text-xl font-bold uppercase">SUBMIT LEVEL FOR LIST VERIFICATION</h2>
        <button onClick={() => setShowSubmitModal(true)} className="bg-black text-white text-xs font-bold px-4 py-2 uppercase">
          + NEW SUBMISSION
        </button>
      </div>

      {/* Submissions List */}
      <div className="space-y-4">
        {submissions.length === 0 ? (
          <div className="text-center py-10 text-xs font-mono text-gray-400 border border-dashed">
            NO SUBMISSIONS YET. CLICK '+ NEW SUBMISSION' TO SUBMIT YOUR LEVEL.
          </div>
        ) : (
          submissions.map(s => (
            <div key={s.id} className="border p-4 flex justify-between items-center">
              <div>
                <div className="font-bold">{s.levelName} (ID: {s.levelId})</div>
                <div className="text-xs text-gray-500">Creator: {s.creator} | Submitted on: {s.date}</div>
                <a href={s.videoUrl} target="_blank" className="text-xs underline text-blue-600">Watch Proof Video</a>
              </div>
              <span className="bg-yellow-100 text-yellow-800 text-xs font-bold px-3 py-1 border border-yellow-300">
                {s.status}
              </span>
            </div>
          ))
        )}
      </div>

      {/* Modal Submit */}
      {showSubmitModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white border-2 border-black p-6 w-full max-w-md space-y-4">
            <h3 className="text-lg font-bold uppercase border-b pb-2">SUBMIT YOUR LEVEL</h3>
            <form onSubmit={handleCreateSubmission} className="space-y-3">
              <div>
                <label className="block text-xs font-bold mb-1">LEVEL NAME</label>
                <input type="text" required className="w-full border p-2 text-sm" value={newSubmission.levelName} onChange={e => setNewSubmission({...newSubmission, levelName: e.target.value})} />
              </div>
              <div>
                <label className="block text-xs font-bold mb-1">LEVEL ID</label>
                <input type="text" required className="w-full border p-2 text-sm" value={newSubmission.levelId} onChange={e => setNewSubmission({...newSubmission, levelId: e.target.value})} />
              </div>
              <div>
                <label className="block text-xs font-bold mb-1">CREATOR NAME</label>
                <input type="text" required className="w-full border p-2 text-sm" value={newSubmission.creator} onChange={e => setNewSubmission({...newSubmission, creator: e.target.value})} />
              </div>
              <div>
                <label className="block text-xs font-bold mb-1">YOUTUBE PROOF URL</label>
                <input type="url" required className="w-full border p-2 text-sm" value={newSubmission.videoUrl} onChange={e => setNewSubmission({...newSubmission, videoUrl: e.target.value})} />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button type="button" onClick={() => setShowSubmitModal(false)} className="px-4 py-2 text-xs border uppercase">CANCEL</button>
                <button type="submit" className="px-4 py-2 text-xs bg-black text-white font-bold uppercase">SUBMIT</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

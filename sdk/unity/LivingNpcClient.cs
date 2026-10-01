using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

namespace LivingNPC
{
    [Serializable] public class NPCEvent { public string text; }
    [Serializable] public class WorldTick { public string world_id; public int tick; public int npcs; public double timestamp; }

    public class LivingNpcClient : MonoBehaviour
    {
        [SerializeField] private string baseUrl = "http://127.0.0.1:8000";
        public string BaseUrl => baseUrl;

        public IEnumerator SendEvent(string npcId, string text, Action<string> onComplete)
        {
            var payload = JsonUtility.ToJson(new NPCEvent { text = text });
            using var request = new UnityWebRequest($"{baseUrl}/npcs/{npcId}/events", "POST");
            request.uploadHandler = new UploadHandlerRaw(Encoding.UTF8.GetBytes(payload));
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            yield return request.SendWebRequest();
            if (request.result == UnityWebRequest.Result.Success) onComplete?.Invoke(request.downloadHandler.text);
            else Debug.LogError(request.error);
        }

        public IEnumerator Tick(Action<WorldTick> onComplete)
        {
            using var request = UnityWebRequest.PostWwwForm($"{baseUrl}/ticks", "");
            yield return request.SendWebRequest();
            if (request.result == UnityWebRequest.Result.Success)
                onComplete?.Invoke(JsonUtility.FromJson<WorldTick>(request.downloadHandler.text));
            else Debug.LogError(request.error);
        }
    }
}

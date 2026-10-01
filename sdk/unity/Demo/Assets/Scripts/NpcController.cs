using System.Collections;
using UnityEngine;

namespace LivingNPC
{
    public class NpcController : MonoBehaviour
    {
        [SerializeField] private LivingNpcClient client;
        [SerializeField] private string npcId = "alice";
        public void Observe(string text) => StartCoroutine(client.SendEvent(npcId, text, _ => { }));
    }
}

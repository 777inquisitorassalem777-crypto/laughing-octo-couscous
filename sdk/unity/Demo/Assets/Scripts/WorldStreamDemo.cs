using System.Collections;
using UnityEngine;

namespace LivingNPC
{
    public class WorldStreamDemo : MonoBehaviour
    {
        [SerializeField] private LivingNpcClient client;
        [SerializeField] private float interval = 0.5f;
        private IEnumerator Start()
        {
            while (true)
            {
                yield return client.Tick(t => Debug.Log($"World {t.world_id} tick={t.tick}, NPCs={t.npcs}"));
                yield return new WaitForSeconds(interval);
            }
        }
    }
}

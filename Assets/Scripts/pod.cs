using UnityEngine;
using UnityEngine.Events;

public class Pod : MonoBehaviour
{
        private SpriteRenderer spriteRenderer;
    public Color color;
    private void Start() {
        spriteRenderer = GetComponent<SpriteRenderer>();
    }
    // Start is called before the first frame update
    public UnityEvent OnPlayerEnter;
    private void OnTriggerEnter2D(Collider2D other) {
        if (other.gameObject.CompareTag("Player"))
        {
            OnPlayerEnter?.Invoke();
            spriteRenderer.color = color;
        }
    }
}
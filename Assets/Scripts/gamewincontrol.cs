using UnityEngine;
using UnityEngine.Events;

public class GameWinControl : MonoBehaviour
{
    public UnityEvent OnWin;
    public int PodsCount = 4;
    private int currentpod = 0;

    public void OnActivate()
    {
        currentpod++;
        if (currentpod >= PodsCount)
        {
            OnWin?.Invoke();
        }
    }
}

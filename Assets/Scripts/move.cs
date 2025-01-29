using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class move : MonoBehaviour
{
    public bool canMove = true;
    Rigidbody2D rb;

    public void cantmove()
    {
        canMove = false;
    }
    // Start is called before the first frame update
    void Start()
    {
        rb = GetComponent<Rigidbody2D>();   
    }

    // Update is called once per frame
    void Update()
    {
        if (canMove)
        {
            rb.velocity = (new Vector3(Input.GetAxisRaw("Horizontal"), Input.GetAxisRaw("Vertical"), 0).normalized * 5);
        }
        else
        {
            rb.velocity = Vector3.zero;
        }
    }
}

using Entitas;
using UnityEngine;

public class PlayerMovement : MonoBehaviour {
    // Game parameters
    public float moveSpeed = 5f;
    private Vector2 _movement;
    private bool _isMoving = true;

    // Reference to the player entity
    private Entity _playerEntity;

    // Boundary values (for keeping player within screen)
    public float minX = -5f;
    public float maxX = 5f;
    public float minY = -5f;
    public float maxY = 5f;

    void Start() {
        // Set up player entity from Entitas (assuming it's already created and exists in the context)
        _playerEntity = Contexts.sharedInstance.game.CreateEntity();
        _playerEntity.AddPosition(Vector2.zero);
    }

    void Update() {
        // If player is not allowed to move (after win)
        if (!_isMoving) {
            return;
        }

        // Get input and calculate movement
        _movement.x = Input.GetAxis("Horizontal");
        _movement.y = Input.GetAxis("Vertical");

        // Normalize movement direction
        _movement = _movement.normalized;

        // Apply movement with speed
        Vector2 newPosition = _playerEntity.position.Value + _movement * moveSpeed * Time.deltaTime;

        // Clamp position to boundaries
        newPosition.x = Mathf.Clamp(newPosition.x, minX, maxX);
        newPosition.y = Mathf.Clamp(newPosition.y, minY, maxY);

        // Update player position
        _playerEntity.ReplacePosition(newPosition);
    }

    // This method would be triggered once the player wins, stopping movement.
    public void StopMovement() {
        _isMoving = false;
        // You can also destroy the player if you want it to disappear after winning
        // _playerEntity.Destroy();
    }
}
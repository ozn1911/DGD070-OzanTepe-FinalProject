using Entitas;
using System.Collections.Generic;
using Entitas.Unity;
using UnityEngine;



public class ViewSystems : Feature
{
    public ViewSystems(Contexts contexts) : base("View Systems")
    {
        Add(new AddViewSystem(contexts));
        Add(new RenderSpriteSystem(contexts));
        Add(new RenderPositionSystem(contexts));
        Add(new RenderDirectionSystem(contexts));
    }
}


public class AddViewSystem : ReactiveSystem<GameEntity>
{
    readonly Transform _viewContainer = new GameObject("Game Views").transform;
    readonly GameContext _context;

    public AddViewSystem(Contexts contexts) : base(contexts.game)
    {
        _context = contexts.game;
    }

    protected override ICollector<GameEntity> GetTrigger(IContext<GameEntity> context)
    {
        return context.CreateCollector(GameMatcher.Sprite);
    }

    protected override bool Filter(GameEntity entity)
    {
        return entity.hasSprite && !entity.hasView;
    }

    protected override void Execute(List<GameEntity> entities)
    {
        foreach (GameEntity e in entities)
        {
            GameObject go = new GameObject("Game View");
            go.transform.SetParent(_viewContainer, false);
            e.AddView(go);
            go.Link(e);
        }
    }
}
public class RenderSpriteSystem : ReactiveSystem<GameEntity>
{
    public RenderSpriteSystem(Contexts contexts) : base(contexts.game)
    {
    }

    protected override ICollector<GameEntity> GetTrigger(IContext<GameEntity> context)
    {
        return context.CreateCollector(GameMatcher.Sprite);
    }

    protected override bool Filter(GameEntity entity)
    {
        return entity.hasSprite && entity.hasView;
    }

    protected override void Execute(List<GameEntity> entities)
    {
        foreach (GameEntity e in entities)
        {
            GameObject go = e.view.gameObject;
            SpriteRenderer sr = go.GetComponent<SpriteRenderer>();
            if (sr == null) sr = go.AddComponent<SpriteRenderer>();
            sr.sprite = Resources.Load<Sprite>(e.sprite.name);
        }
    }
}
public class RenderPositionSystem : ReactiveSystem<GameEntity>
{
    public RenderPositionSystem(Contexts contexts) : base(contexts.game)
    {
    }

    protected override ICollector<GameEntity> GetTrigger(IContext<GameEntity> context)
    {
        return context.CreateCollector(GameMatcher.Position);
    }

    protected override bool Filter(GameEntity entity)
    {
        return entity.hasPosition && entity.hasView;
    }

    protected override void Execute(List<GameEntity> entities)
    {
        foreach (GameEntity e in entities)
        {
            e.view.gameObject.transform.position = e.position.value;
        }
    }
}
public class RenderDirectionSystem : ReactiveSystem<GameEntity>
{
    readonly GameContext _context;

    public RenderDirectionSystem(Contexts contexts) : base(contexts.game)
    {
        _context = contexts.game;
    }

    protected override ICollector<GameEntity> GetTrigger(IContext<GameEntity> context)
    {
        return context.CreateCollector(GameMatcher.Direction);
    }

    protected override bool Filter(GameEntity entity)
    {
        return entity.hasDirection && entity.hasView;
    }

    protected override void Execute(List<GameEntity> entities)
    {
        foreach (GameEntity e in entities)
        {
            float ang = e.direction.value;
            e.view.gameObject.transform.rotation = Quaternion.AngleAxis(ang - 90, Vector3.forward);
        }
    }
}


public class MoveSystem : IExecuteSystem, ICleanupSystem
{
    readonly IGroup<GameEntity> _moves;
    readonly IGroup<GameEntity> _moveCompletes;
    const float _speed = 4f;

    public MoveSystem(Contexts contexts)
    {
        _moves = contexts.game.GetGroup(GameMatcher.Move);
        _moveCompletes = contexts.game.GetGroup(GameMatcher.MoveComplete);
    }

    public void Execute()
    {
        foreach (GameEntity e in _moves.GetEntities())
        {
            Vector2 dir = e.move.target - e.position.value;
            Vector2 newPosition = e.position.value + dir.normalized * _speed * Time.deltaTime;
            e.ReplacePosition(newPosition);

            float angle = Mathf.Atan2(dir.y, dir.x) * Mathf.Rad2Deg;
            e.ReplaceDirection(angle);

            float dist = dir.magnitude;
            if (dist <= 0.5f)
            {
                e.RemoveMove();
                e.isMoveComplete = true;
            }
        }
    }

    public void Cleanup()
    {
        foreach (GameEntity e in _moveCompletes.GetEntities())
        {
            e.isMoveComplete = false;
        }
    }
}

public class MovementSystems : Feature
{
    public MovementSystems(Contexts contexts) : base("Movement Systems")
    {
        Add(new MoveSystem(contexts));
    }
}


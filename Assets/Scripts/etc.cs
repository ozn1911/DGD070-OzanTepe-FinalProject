using Entitas;
using Entitas.CodeGeneration.Attributes;
using System.Collections.Generic;
using UnityEngine;

[Game]
public class PositionComponent : IComponent
{
    public Vector2 value;
}

[Game]
public class DirectionComponent : IComponent
{
    public float value;
}

[Game]
public class ViewComponent : IComponent
{
    public GameObject gameObject;
}

[Game]
public class SpriteComponent : IComponent
{
    public string name;
}

[Game]
public class MoverComponent : IComponent
{
}

[Game]
public class MoveComponent : IComponent
{
    public Vector2 target;
}

[Game]
public class MoveCompleteComponent : IComponent
{
}
[Input, Unique]
public class LeftMouseComponent : IComponent
{
}

[Input, Unique]
public class RightMouseComponent : IComponent
{
}

[Input]
public class MouseDownComponent : IComponent
{
    public Vector2 position;
}

[Input]
public class MousePositionComponent : IComponent
{
    public Vector2 position;
}

[Input]
public class MouseUpComponent : IComponent
{
    public Vector2 position;
}

public class CommandMoveSystem : ReactiveSystem<InputEntity>
{
    readonly GameContext _gameContext;
    readonly IGroup<GameEntity> _movers;

    public CommandMoveSystem(Contexts contexts) : base(contexts.input)
    {
        _movers = contexts.game.GetGroup(GameMatcher.AllOf(GameMatcher.Mover).NoneOf(GameMatcher.Move));
    }

    protected override ICollector<InputEntity> GetTrigger(IContext<InputEntity> context)
    {
        return context.CreateCollector(InputMatcher.AllOf(InputMatcher.LeftMouse, InputMatcher.MouseDown));
    }

    protected override bool Filter(InputEntity entity)
    {
        return entity.hasMouseDown;
    }

    protected override void Execute(List<InputEntity> entities)
    {
        foreach (InputEntity e in entities)
        {
            GameEntity[] movers = _movers.GetEntities();
            if (movers.Length <= 0) return;
            movers[Random.Range(0, movers.Length)].ReplaceMove(e.mouseDown.position);
        }
    }
}

public class InputSystems : Feature
{
    public InputSystems(Contexts contexts) : base("Input Systems")
    {
        Add(new EmitInputSystem(contexts));
        Add(new CreateMoverSystem(contexts));
        Add(new CommandMoveSystem(contexts));
    }         
}
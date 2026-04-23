from dataclasses import dataclass
from models.singlepick import (
    SinglePickConfig,
    PickersConfig,
    WheelConfig,
    JackpotPick,
    FixedJackpot,
    CIJackpot,
    RtpSPReward,
    RewardPick,
    RetryPick,
)


@dataclass
class ValidationError:
    configset_name: str
    field: str
    message: str


def validate_configset_name(name: str, existing_names: list[str]) -> str | None:
    """Возвращает сообщение об ошибке или None если имя валидно."""
    if not name:
        return "Имя ConfigSet не может быть пустым"
    if name in existing_names:
        return f"ConfigSet с именем '{name}' уже существует"
    return None


def is_percentage_valid(percentage: float) -> bool:
    """Проверяет что значение имеет не более 3 знаков после запятой (шаг 0.001).
    Схема указывает multipleOf: 0.01, но реальные конфиги используют значения
    вроде 0.028 (3 знака), поэтому допускаем до 3 знаков включительно."""
    s = f"{percentage:.10f}".rstrip("0")
    if "." not in s:
        return True
    decimals = len(s.split(".")[1])
    return decimals <= 3


def validate_singlepick(config: SinglePickConfig) -> list[ValidationError]:
    errors: list[ValidationError] = []

    for name, configset in config.config_sets.items():
        # 1. Имя ConfigSet непусто
        if not name:
            errors.append(ValidationError(
                configset_name=name,
                field="name",
                message="Имя ConfigSet не может быть пустым",
            ))

        content = configset.content

        if isinstance(content, PickersConfig):
            # 3. PickersConfig содержит ≥ 1 пик
            if not content.picks:
                errors.append(ValidationError(
                    configset_name=name,
                    field="Picks",
                    message="Список пиков не может быть пустым",
                ))

            # 5. В каждом JackpotPick: min <= max
            for pick in content.picks:
                if isinstance(pick, JackpotPick):
                    jackpot = pick.jackpot
                    if isinstance(jackpot, (FixedJackpot, CIJackpot)):
                        if jackpot.min > jackpot.max:
                            errors.append(ValidationError(
                                configset_name=name,
                                field="JackpotPick.Min/Max",
                                message="Min не может быть больше Max",
                            ))

                # 6. В каждом RtpSPReward: percentage кратно 0.01
                rewards = []
                if isinstance(pick, (RewardPick, RetryPick)):
                    rewards = pick.reward
                for reward in rewards:
                    if isinstance(reward, RtpSPReward):
                        if not is_percentage_valid(reward.percentage):
                            errors.append(ValidationError(
                                configset_name=name,
                                field="RtpReward.Percentage",
                                message="Percentage должно быть кратно 0.01",
                            ))

        elif isinstance(content, WheelConfig):
            # 4. WheelConfig содержит ≥ 1 сектор
            if not content.wedges:
                errors.append(ValidationError(
                    configset_name=name,
                    field="Wedges",
                    message="Список секторов не может быть пустым",
                ))

            # 6. В каждом RtpSPReward внутри Wedge: percentage кратно 0.01
            for wedge in content.wedges:
                for reward in wedge.reward:
                    if isinstance(reward, RtpSPReward):
                        if not is_percentage_valid(reward.percentage):
                            errors.append(ValidationError(
                                configset_name=name,
                                field="RtpReward.Percentage",
                                message="Percentage должно быть кратно 0.01",
                            ))

    return errors

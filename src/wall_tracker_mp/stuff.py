def convert_mp_profiles(profiles):
    return [[sect.steps() for sid, sect in enumerate(p.sections())] for _, p in profiles.items()]


def convert_mp_profiles_with_days(profiles):
    return [[list(zip(sect.days(), sect.steps())) for sid, sect in enumerate(p.sections())] for _, p in profiles.items()]

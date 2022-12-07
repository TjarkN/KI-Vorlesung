# Hier euren algorithmus
def particle_filtering(evidences, n, dbn, samples):
    new_samples = []
    weights = []
    for i in range(n):
        new_samples.append()
        weights.append()
    new_samples = weighted_sample_with_replacements(n, new_samples, weights)
    return new_samples

def weighted_sample_with_replacements(n, s, w):
    samples = []
    for i in range(n):
        samples.append(s[i]*w[i])
    return samples

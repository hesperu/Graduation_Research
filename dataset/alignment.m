function res = alignment(vis,dtm,hil,save_path)
    metric = registration.metric.MattesMutualInformation;
    before_vis = imread(vis);
    dtm_img = imread(dtm);
    hil_img = imread(hil);

    optimizer = registration.optimizer.OnePlusOneEvolutionary;
    metric = registration.metric.MattesMutualInformation;

    optimizer.InitialRadius = 0.0009;
    optimizer.Epsilon = 1.5e-4;
    optimizer.GrowthFactor = 1.01;
    optimizer.MaximumIterations = 100;
    after_hil = imregister(hil_img,dtm_img,'affine',optimizer,metric);
    
    after_vis = imregister(before_vis,after_hil,"affine",optimizer,metric);
    imwrite(after_vis,save_path);

    res = "Success!"
end